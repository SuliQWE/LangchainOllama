import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from .dependencies import get_current_user, get_db
from mysite.database.models import UserProfile, FileObject
from mysite.database.schema import FileObjectResponseSchema

file_router = APIRouter(prefix="/file", tags=["File (Upload)"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_upload(file: UploadFile | None) -> str | None:
    if file is None:
        return None
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return path.replace('\\', '/')


@file_router.post('/', response_model=FileObjectResponseSchema)
async def create_file(
    dataset_file: UploadFile = File(...),
    task_file: UploadFile | None = File(None),
    image_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    if not dataset_file.filename and (image_file is None or not image_file.filename):
        raise HTTPException(status_code=400, detail='Пустое сообщение нельзя отправить')

    file_obj = FileObject(
        dataset_file=save_upload(dataset_file),
        task_file=save_upload(task_file),
        image_file=save_upload(image_file),
        user_id=current_user.id,
    )
    db.add(file_obj)
    db.commit()
    db.refresh(file_obj)
    return file_obj


@file_router.get('/', response_model=list[FileObjectResponseSchema])
async def get_files(
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    return (
        db.query(FileObject)
        .filter(FileObject.user_id == current_user.id)
        .order_by(FileObject.created_date.desc())
        .all()
    )


@file_router.get('/{file_id}/', response_model=FileObjectResponseSchema)
async def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    file_obj = db.query(FileObject).filter(FileObject.id == file_id).first()
    if not file_obj:
        raise HTTPException(status_code=404, detail='Файл не найден')
    if file_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Вы можете смотреть только свои файлы')
    return file_obj


@file_router.put('/{file_id}/', response_model=dict)
async def update_file(
    file_id: int,
    dataset_file: UploadFile | None = File(None),
    task_file: UploadFile | None = File(None),
    image_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    if (dataset_file is None or not dataset_file.filename) and (image_file is None or not image_file.filename):
        raise HTTPException(status_code=400, detail='Пустое сообщение нельзя отправить')

    file_obj = db.query(FileObject).filter(FileObject.id == file_id).first()
    if not file_obj:
        raise HTTPException(status_code=404, detail='Файл не найден')
    if file_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Вы можете изменять только свой файл')

    if dataset_file is not None:
        file_obj.dataset_file = save_upload(dataset_file)
    if task_file is not None:
        file_obj.task_file = save_upload(task_file)
    if image_file is not None:
        file_obj.image_file = save_upload(image_file)

    db.commit()
    return {'message': 'Файл успешно изменен'}


@file_router.delete('/{file_id}/', response_model=dict)
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    file_obj = db.query(FileObject).filter(FileObject.id == file_id).first()
    if not file_obj:
        raise HTTPException(status_code=404, detail='Файл не найден')
    if file_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Вы можете удалить только свой файл')

    db.delete(file_obj)
    db.commit()
    return {'message': 'Файл успешно удален'}