from flask_restx import Namespace, Resource, fields, marshal
from flask import request
from http import HTTPStatus
import json

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}
namespace = Namespace('',
                      'Task Manager operations',
                      security='apiKey',
                      authorizations=authorizations)

@namespace.route('/login')
class Login(Resource):
    @namespace.response(500, 'Internal Server error')
    @namespace.expect(
        namespace.model(
            'logining',
            {
                'phone_number': fields.String(),
                'password': fields.String()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'login_answer',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Вход в аккаунт'''
        return


@namespace.route('/registration')
class Registration(Resource):
    @namespace.response(500, 'Internal Server error')
    @namespace.expect(
        namespace.model(
            'registration',
            {
                "phone_number": fields.String(),
                "password": fields.String(),
                "password_confirm": fields.String()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            "register_answer",
            {
                "status": fields.String(),
                "access_token": fields.String()
            }
        )
    )
    def post(self):
        '''Регистрация нового пользователя'''
        return


@namespace.route('/logout')
class Logout(Resource):
    @namespace.response(500, 'Internal server error')
    @namespace.marshal_with(
        namespace.model(
            'logout',
            {
                "status": fields.String()
            }
        )
    )
    def post(self):
        '''Аннулирование предыдущих токенов аутентификации'''
        return


@namespace.route('/profile/info')
class ProfileInfo(Resource):
    @namespace.doc(security='apiKey')
    @namespace.marshal_with(
        namespace.model(
            'ProfileInfoResponse',
            {
                'access_token': fields.String(),
                'status': fields.String(),
                'data': fields.Nested(
                    namespace.model(
                        'ProfileInfoData',
                        {
                            'profile': fields.Nested(
                                namespace.model(
                                    'ProfileInfo',
                                    {
                                        'user_id': fields.Integer(required=True),
                                        'username': fields.String(required=False),
                                        'phone_number': fields.String(required=True),
                                        'email': fields.String(required=False),
                                        'yandex_mail': fields.String(required=False),
                                        'telegram_id': fields.String(required=False)
                                    }
                                )
                            )
                        }
                    )
                )
            }
        )
    )
    def get(self):
        '''Показывает доступную информацию о пользователе по токену аутентификации'''
        return


@namespace.route('/user/info')
class UserInfo(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'UserInfoGet',
            {
                'user_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'UserInfoResponse',
            {
                'status': fields.String(),
                'data': fields.Nested(
                    namespace.model(
                        'UserInfoData',
                        {
                            'user': fields.Nested(
                                namespace.model(
                                    'UserInfo',
                                    {
                                        'username': fields.String(),
                                        'user_id': fields.Integer()
                                    }
                                )
                            )
                        }
                    )
                )
            }
        )
    )
    def get(self):
        '''Возвращает информацию о пользователе'''
        return


@namespace.route('/profile/boards')
class ProfileBoards(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'GetProfileBoards',
            {
                'token': fields.String(),
                'user_id': fields.Integer(),
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'ProfileBoardsResponse',
            {
                "token": fields.String(),
                "data": fields.Nested(
                    namespace.model(
                        'ProfileBoardsData',
                        {
                            'boards': fields.List(
                                fields.Nested(
                                    namespace.model(
                                        'ProfileBoards',
                                        {
                                            'board_id': fields.Integer(),
                                            'boardname': fields.String(),
                                            'color': fields.String(),
                                            'description': fields.String(),
                                            'user_id': fields.Integer(),
                                            'user_position': fields.String(description='Роль пользователя на доске')
                                        }
                                    )
                                )
                            )
                        }
                    )
                )
            }
        )
    )
    def get(self):
        '''Возваращает доски пользователя'''
        return


@namespace.route('/profile/edit', methods=['POST'])
class ProfileEdit(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'PostProfileEdit',
            {
                'changes': fields.Nested(
                    namespace.model(
                        'Changes',
                        {
                            'username': fields.String(),
                            'phone_number': fields.String(),
                            'email': fields.String(),
                            'telegram_id': fields.String(),
                            'password': fields.String()
                        }
                    ),
                ),
                'old_password': fields.String()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'ProfileEditResponse',
            {
                'access_token': fields.String(),
                'status': fields.String()
            }
        )
    )
    def post(self):
        '''Изменяет профиль пользователя'''
        return


@namespace.route('/board/info')
class BoardInfo(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'GetBoardInfo',
            {
                'board_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'BoardInfoResponse',
            {
                'status': fields.String(),
                'access_token': fields.String(),
                'data': fields.Nested(
                    namespace.model(
                        'BoardData',
                        {
                            'board': fields.Nested(
                                namespace.model(
                                    'Board',
                                    {
                                        'board_id': fields.Integer(),
                                        'boardname': fields.String(),
                                        'deadline': fields.Date(),
                                        'color': fields.String(),
                                        'description': fields.String()
                                    }
                                )
                            )
                        }
                    )
                )
            }
        )
    )
    def get(self):
        '''Возвращает информацию о доске'''
        return


@namespace.route('/board/tasks')
class BoardTasks(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'GetBoardTasks',
            {
                'board_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'BoardTasksResponse',
            {
                'status': fields.String(),
                'access_token': fields.String(),
                'data': fields.Nested(
                    namespace.model(
                        'BoardTasksData',
                        {
                            'tasks': fields.List(
                                fields.Nested(
                                    namespace.model(
                                        'BoardTasks',
                                        {
                                            'task_id': fields.Integer(),
                                            'taskname': fields.String(),
                                            'board_id': fields.Integer(),
                                            'description': fields.String(),
                                            'deadline': fields.Date(),
                                            'stage': fields.Integer(),
                                            'author_id': fields.Integer()
                                        }
                                    )
                                )
                            )
                        }
                    )
                )
            }
        )
    )
    def get(self):
        '''Возвращает задачи прикрепленные к доске'''
        return


@namespace.route('/task/info')
class TaskInfo(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TaskInfoGet',
            {
                'task_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TaskInfoResponse',
            {
                'status': fields.String(),
                'access_token': fields.String(),
                'data': fields.Nested(
                    namespace.model(
                        'TaskInfoData',
                        {
                            'task': fields.Nested(
                                namespace.model(
                                    'TaskInfo',
                                    {
                                        'task_id': fields.Integer(),
                                        'taskname': fields.String(),
                                        'board_id': fields.Integer(),
                                        'description': fields.String(),
                                        'stage': fields.Integer(),
                                        'author_id': fields.Integer(),
                                        'deadline': fields.Date()
                                    }
                                )
                            )
                        }
                    )
                )
            }
        )
    )
    def get(self):
        '''Возвращает информацию о задании'''
        return


@namespace.route('/task/users')
class TaskUsers(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TaskUsersGet',
            {
                'task_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TaskUsersResponse',
            {
                'status': fields.String(),
                'access_token': fields.String(),
                'data': fields.Nested(
                    namespace.model(
                        'TaskUsersData',
                        {
                            'users': fields.List(
                                fields.Nested(
                                    namespace.model(
                                        'TaskUsers',
                                        {
                                            'task_id': fields.Integer(),
                                            'user_id': fields.Integer(),
                                            'user_position': fields.String()
                                        }
                                    )
                                )
                            )
                        }
                    )
                )
            }
        )
    )
    def get(self):
        '''Возвращает пользователей, прикрепленных к заданию'''
        return


@namespace.route('/task/comments')
class TaskComments(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TaskCommentsGet',
            {
                'task_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TaskCommentsResponse',
            {
                'status': fields.String(),
                'access_token': fields.String(),
                'data': fields.Nested(
                    namespace.model(
                        'TaskCommentsData',
                        {
                            'comments': fields.List(
                                fields.Nested(
                                    namespace.model(
                                        'TaskComments',
                                        {
                                            'task_id': fields.Integer(),
                                            'comments_id': fields.Integer(),
                                            'content': fields.String(),
                                            'date_time': fields.DateTime(),
                                            'author_id': fields.Integer(),
                                            'board_id': fields.Integer()
                                        }
                                    )
                                )
                            )
                        }
                    )
                )
            }
        )
    )
    def get(self):
        '''Возвращает комментарии, написанные под задачей'''
        return


@namespace.route('/task/files')
class TaskFiles(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TaskFilesGet',
            {
                'task_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TaskFilesResponse',
            {
                'status': fields.String(),
                'access_token': fields.String(),
                'data': fields.Nested(
                    namespace.model(
                        'TaskFilesData',
                        {
                            'files': fields.List(
                                fields.Nested(
                                    namespace.model(
                                        'TaskFiles',
                                        {
                                            'file_id': fields.Integer(),
                                            'task_id': fields.Integer(),
                                            'filename': fields.DateTime(),
                                            'author_id': fields.Integer()
                                        }
                                    )
                                )
                            )
                        }
                    )
                )
            }
        )
    )
    def get(self):
        '''Возвращает файлы, прикрепленные к задаче'''
        return

@namespace.route('/add/board')
class AddBoard(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'AddBoardPost',
            {
                'boardname': fields.String(),
                'deadline': fields.Date(),
                'color': fields.String(),
                'description': fields.String(),
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'AddBoardResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Создает новую доску'''
        return

@namespace.route('/add/task')
class AddTask(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'AddTaskPost',
            {
                'board_id': fields.Integer(),
                'taskname': fields.String(),
                'deadline': fields.Date(),
                'color': fields.String(),
                'description': fields.String(),
                'stage': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'AddTaskResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Создает новое задание на доске'''
        return


@namespace.route('/board/edit')
class BoardEdit(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'BoardEditPost',
            {
                'boardname': fields.String(),
                'deadline': fields.Date(),
                'color': fields.String(),
                'description': fields.String(),
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'BoardEditResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Изменяет доску'''
        return

@namespace.route('/board/add/user')
class BoardAddUser(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'BoardAddUserPost',
            {
                'board_id': fields.String(),
                'user_id': fields.Date(),
                'user_position': fields.String()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'BoardAddUserResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Добавляет пользователя на доску'''
        return

@namespace.route('/board/delete/user')
class BoardDeleteUser(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'BoardDeleteUserPost',
            {
                'board_id': fields.String(),
                'user_id': fields.Date()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'BoardDeleteUserResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Удаляет пользователя с доски'''
        return


@namespace.route('/task/edit')
class TaskEdit(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TaskEditPost',
            {
                'board_id': fields.Integer(),
                'taskname': fields.String(),
                'deadline': fields.Date(),
                'color': fields.String(),
                'description': fields.String(),
                'stage': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TaskEditResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Изменяет задание'''
        return

@namespace.route('/task/add/comment')
class TaskAddComment(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TaskAddCommentPost',
            {
                'task_id': fields.Integer(),
                'content': fields.String()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TaskAddCommentResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Добавляет комментарий к заданию'''
        return

@namespace.route('/task/delete/comment')
class TaskDeleteComment(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TaskDeleteCommentPost',
            {
                'comment_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TaskDeleteCommentResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Удаляет комментарий к заданию'''
        return


@namespace.route('/task/add/user')
class TaskAddUser(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TaskAddUserPost',
            {
                'task_id': fields.String(),
                'user_id': fields.Date(),
                'user_position': fields.String()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TaskAddUserResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Прикрепляет пользователя к заданию'''
        return

@namespace.route('/task/delete/user')
class TaskDeleteUser(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TaskDeleteUserPost',
            {
                'task_id': fields.String(),
                'user_id': fields.Date()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TaskDeleteUserResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Удаляет пользователя к заданию'''
        return

@namespace.route('/delete/board')
class DeleteBoard(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'DeleteBoardPost',
            {
                'board_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'DeleteBoardResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Удаляет пользователя к заданию'''
        return

@namespace.route('/delete/task')
class DeleteTask(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'DeleteTaskPost',
            {
                'task_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'DeleteTaskResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Удаляет пользователя к заданию'''
        return

from flask_restx import reqparse
from werkzeug.datastructures import FileStorage
upload_parser = reqparse.RequestParser()
upload_parser.add_argument('files', location='files',
                           type=FileStorage, required=True, action="append")
upload_parser.add_argument('task_id', type=int)

@namespace.route('/task/add/file')
class TaskAddFile(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(upload_parser)
    @namespace.marshal_with(
        namespace.model(
            'DeleteTaskResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Добавляет файл к заданию'''
        return


parser = namespace.parser()
parser.add_argument('param', type=int, help='Some param', location='form')
parser.add_argument('in_files', type=FileStorage, location='files')
@namespace.route('/task/get/file')
class TaskGetFile(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TaskGetFileGet',
            {
                'file_id': fields.Integer()
            }
        )
    )
    @namespace.doc(models=parser)
    # @namespace.header('file')
    def get(self):
        '''Получает файл (я не нашел способа описать это в API с помощью flask-restx'''
        return

@namespace.route('/task/delete/file')
class TaskDeleteFile(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TaskDeleteFileGet',
            {
                'file_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TaskDeleteFileResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Удаляет файл'''
        return

@namespace.route('/trashcan/add/task')
class TrashcanAddTask(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TrashcanAddTaskGet',
            {
                'task_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TrashcanAddTaskResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Помещает задание в корзину'''
        return


@namespace.route('/trashcan/get/tasks')
class TrashcanGetTasks(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TrashcanGetTasksGet',
            {
                'board_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TrashcanGetTasksResponse',
            {
                'status': fields.String(),
                'access_token': fields.String(),
                'data': fields.Nested(
                    namespace.model(
                        'TrashcanGetTaskData',
                        {
                            'task': fields.List(
                                    fields.Nested(
                                    namespace.model(
                                        'TrashcanGetTask',
                                        {
                                            'task_id': fields.Integer(),
                                            'taskname': fields.String(),
                                            'board_id': fields.Integer(),
                                            'description': fields.String(),
                                            'stage': fields.Integer(),
                                            'author_id': fields.Integer(),
                                            'deadline': fields.Date()
                                        }
                                    )
                                )
                            )
                        }
                    )
                )
            }
        )
    )
    def get(self):
        '''Возвращает информацию о всех заданиях на доске, которые находятся в корзине'''
        return


@namespace.route('/trashcan/restore/task')
class TrashcanRestoreTask(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TrashcanRestoreTaskGet',
            {
                'task_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TrashcanRestoreTaskResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Восстанавливает задание'''
        return

@namespace.route('/trashcan/delete/task')
class TrashcanDeleteTask(Resource):
    @namespace.doc(security='apiKey')
    @namespace.expect(
        namespace.model(
            'TrashcanDeleteTaskGet',
            {
                'task_id': fields.Integer()
            }
        )
    )
    @namespace.marshal_with(
        namespace.model(
            'TrashcanDeleteTaskResponse',
            {
                'status': fields.String(),
                'access_token': fields.String()
            }
        )
    )
    def post(self):
        '''Удаляет файл навсегда'''
        return