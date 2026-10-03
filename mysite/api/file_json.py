from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .dependencies import get_current_user, get_db
from mysite.database.models import UserProfile, FileObject
from mysite.database.schema import FileObjectCreateSchema, FileObjectResponseSchema

file_router = APIRouter(prefix="/file", tags=["File (JSON)"])


@file_router.post('/', response_model=FileObjectResponseSchema)
async def create_file(
    data: FileObjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    if not (data.dataset_file and data.dataset_file.strip()) and not (data.image_file and data.image_file.strip()):
        raise HTTPException(status_code=400, detail='Пустое сообщение нельзя отправить')

    file_obj = FileObject(
        dataset_file=data.dataset_file,
        task_file=data.task_file,
        image_file=data.image_file,
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
    data: FileObjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    if not (data.dataset_file and data.dataset_file.strip()) and not (data.image_file and data.image_file.strip()):
        raise HTTPException(status_code=400, detail='Пустое сообщение нельзя отправить')

    file_obj = db.query(FileObject).filter(FileObject.id == file_id).first()
    if not file_obj:
        raise HTTPException(status_code=404, detail='Файл не найден')
    if file_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Вы можете изменять только свой файл')

    file_obj.dataset_file = data.dataset_file
    file_obj.task_file = data.task_file
    file_obj.image_file = data.image_file
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