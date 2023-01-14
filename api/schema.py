import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
import graphql_jwt
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id
from django.contrib.auth.models import User
from .models import Profile, Message


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            "username": ["exact", "icontains"],
        }
        interfaces = (relay.Node,)


class ProfileNode(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = {
            "user_prof__username": ["icontains"],
        }
        interfaces = (relay.Node,)


class MessageNode(DjangoObjectType):
    class Meta:
        model = Message
        filter_fields = {
            "sender": ["exact"],
            "receiver": ["exact"],
        }
        interfaces = (relay.Node,)


class CreateUserMutation(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    user = graphene.Field(UserNode)

    def mutate_and_get_payload(root, info, **input):
        user = User(
            username=input.get("username"),
            email=input.get("email"),
        )
        user.set_password(input.get("password"))
        user.save()

        return CreateUserMutation(user=user)


class CreateProfileMutation(relay.ClientIDMutation):
    profile = graphene.Field(ProfileNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        profile = Profile(
            user_prof_id=info.context.user.id
        )
        profile.save()

        return CreateProfileMutation(profile=profile)


class UpdateProfileMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        friends = graphene.List(graphene.ID)
        friend_requests = graphene.List(graphene.ID)

    profile = graphene.Field(ProfileNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        profile = Profile.objects.get(id=from_global_id(input.get("id"))[1])

        if input.get("friends") is not None:
            friends_set = []
            for friend in input.get("friends"):
                friend_id = from_global_id(friend)[1]
                friend_object = User.objects.get(id=friend_id)
                friends_set.append(friend_object)
            profile.friends.set(friends_set)
        if input.get("friend_requests") is not None:
            friend_requests_set = []
            for friend_request in input.get("friend_requests"):
                friend_request_id = from_global_id(friend_request)[1]
                friend_request_object = User.objects.get(id=friend_request_id)
                friend_requests_set.append(friend_request_object)
            profile.friend_requests.set(friend_requests_set)
        profile.save()

        return UpdateProfileMutation(profile=profile)


class CreateMessageMutation(relay.ClientIDMutation):
    class Input:
        message = graphene.String(required=True)
        receiver = graphene.ID(required=True)

    message = graphene.Field(MessageNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        message = Message(
            message=input.get("message"),
            sender_id=info.context.user.id,
            receiver_id=from_global_id(input.get("receiver"))[1]
        )
        message.save()

        return CreateMessageMutation(message=message)


class Query(graphene.ObjectType):
    profile = graphene.Field(ProfileNode)
    all_users = DjangoFilterConnectionField(UserNode)
    all_profiles = DjangoFilterConnectionField(ProfileNode)
    all_messages = DjangoFilterConnectionField(MessageNode)

    @login_required
    def resolve_profile(self, info, **kwargs):
        return Profile.objects.get(user_prof=info.context.user.id)

    @login_required
    def resolve_all_users(self, info, **kwargs):
        return User.objects.all()

    @login_required
    def resolve_all_profiles(self, info, **kwargs):
        return Profile.objects.all()

    @login_required
    def resolve_all_messages(self, info, **kwargs):
        return Message.objects.all()


class Mutation(graphene.ObjectType):
    create_user = CreateUserMutation.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    create_profile = CreateProfileMutation.Field()
    update_profile = UpdateProfileMutation.Field()
    create_message = CreateMessageMutation.Field()
