from fastapi import FastAPI
from starlette.graphql import GraphQLApp
import graphene

from schema import PostSchema, PostModel
from models import Post
from db_conf import db_session

app = FastAPI()
db = db_session.session_factory()


class Query(graphene.ObjectType):
    all_posts = graphene.List(PostModel)
    post_by_id = graphene.Field(PostModel, post_id=graphene.Int(required=True))

    def resolve_all_posts(self, info):
        query = PostModel.get_query(info)
        return query.all()

    def resolve_post_by_id(self, info, post_id):
        return db.query(Post).filter(Post.id == post_id).first()


class CreateNewPost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, title, content):
        post = PostSchema(title=title, content=content)
        db_post = Post(title=post.title, content=post.content)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return CreateNewPost(ok=True)


class PostMutations(graphene.ObjectType):
    create_new_post = CreateNewPost.Field()


app.add_route("/graphql", GraphQLApp(schema=graphene.Schema(mutation=PostMutations, query=Query)))
