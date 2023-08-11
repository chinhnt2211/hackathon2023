from flask import request, jsonify, make_response, Response
from flask_restx import Resource, Namespace
from database import postgres_session
from database import Profile as ProfileEntity
from database import Step as StepEntity
from utils import data_time_serialize, allowed_file
from minio import Minio
import uuid
from configs.env import MINIO_HOST, MINIO_PORT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME
from configs.constant import PROFILE_STATUS_WAITING, PROFILE_STATUS_PROCESSING, PROFILE_STATUS_DONE, ATTACHMENT_AVAILABLE
import os

api = Namespace("profiles", description="Profiles API", path="/")

MINIO_CLIENT = Minio(MINIO_HOST, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=True)


@api.route(f"/profiles")
class ProfilesApi(Resource):
    @api.doc("Get profiles")
    @api.response(200, "Success")
    @api.response(500, "Internal Server Error")
    def get(self):
        """Search Profiles"""
        try:
            args = request.args
            profile_status_param = args.get('profile_status', '').strip(',')
            # step_type_param = args.get('step_type', '').strip(',')

            profiles = postgres_session.query(ProfileEntity)
            if bool(profile_status_param):
                profile_status_list = [int(status) for status in profile_status_param.split(',')]
                profiles = profiles.filter(
                    ProfileEntity.profile_status.in_(profile_status_list)
                )

            # if bool(step_type_param):
            #     step_type_list = [int(step_type) for step_type in step_type_param.split(',')]
            #     steps = postgres_session.query(StepEntity).filter
            #     profiles = profiles.filter(
            #         ProfileEntity.profile_status.in_(step_type_list)
            #     )

            profiles = profiles.all()

            data = []
            if profiles:
                for profile in profiles:
                    each = data_time_serialize(profile.serialize) if profile else profile
                    steps = postgres_session.query(StepEntity).filter(
                        StepEntity.profile_id == profile.id
                    ).all()
                    each["steps"] = data_time_serialize([s.serialize for s in steps])
                    data.append(each)

                return make_response(jsonify({"data": data, "message": "Success"}), 200)
            else:
                return make_response(jsonify({"data": [], "message": "Success"}), 200)
        except Exception as e:
            print(e)
            return make_response(jsonify({"data": None, "message": "Internal Server Error"}), 500)


@api.route(f"/profiles/<string:profile_id>")
class ProfileApi(Resource):

    @api.doc("Get profile")
    @api.response(200, "Success")
    @api.response(400, "Invalid API parameters")
    @api.response(500, "Internal Server Error")
    def get(self, profile_id):
        """Get profile"""
        try:
            data = {}

            profile = postgres_session.query(ProfileEntity).filter(
                ProfileEntity.id == profile_id
            ).first()

            if profile:
                data["profile"] = data_time_serialize(profile.serialize) if profile else profile
                steps = postgres_session.query(StepEntity).filter(
                        StepEntity.profile_id == profile_id
                ).all()
                data["steps"] = data_time_serialize([s.serialize for s in steps])

                return make_response(
                    jsonify({"data": data, "message": "Success"}), 200)
            else:
                return make_response(jsonify({"data": [], "message": "Success"}), 200)
        except Exception as e:
            print(e)
            return make_response(jsonify({"data": None, "message": "Internal Server Error"}), 500)

    @api.doc("Push attachment")
    @api.response(200, "Success")
    @api.response(400, "Invalid API file")
    @api.response(500, "Internal Server Error")
    def post(self, profile_id):
        """Push Attachment"""
        try:
            attachment_file = request.files["attachment_file"]

            if not allowed_file(attachment_file.filename):
                return make_response(jsonify({"data": [], "message": "Invalid API file"}), 400)

            profile = postgres_session.query(ProfileEntity).filter(
                ProfileEntity.id == profile_id
            ).first()

            new_filename = uuid.uuid4().hex + '_' + attachment_file.filename

            print(new_filename)
            attachment_file.save(os.path.dirname(__file__) + "/uploads/" + new_filename)

            MINIO_CLIENT.fput_object(
                MINIO_BUCKET_NAME, new_filename, os.path.dirname(__file__) + "/uploads/" + new_filename
            )

            profile_status = PROFILE_STATUS_PROCESSING
            if profile.profile_status == PROFILE_STATUS_PROCESSING:
                profile_status = PROFILE_STATUS_DONE

            postgres_session.query(ProfileEntity).filter(
                ProfileEntity.id == profile_id
            ).update({
                "profile_status": profile_status
            })

            postgres_session.query(StepEntity).filter(
                StepEntity.id == profile_id,
                StepEntity.attachment_type == profile_status
            ).update({
                "attachment_name": attachment_file.filename,
                "attachment_status": ATTACHMENT_AVAILABLE,
                "attachment_name_file": new_filename
            })

            os.remove(os.path.dirname(__file__) + "/uploads/" + new_filename)

            return make_response(
                jsonify({"message": "Success"}), 200)

        except Exception as e:
            print(e)
            return make_response(jsonify({"data": None, "message": "Internal Server Error"}), 500)

