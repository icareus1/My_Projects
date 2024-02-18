import os
import tempfile
from moviepy.editor import VideoFileClip
import uuid
from django.core.files.base import ContentFile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    try:
        user = request.user

        serializer = PostCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content = serializer.validated_data['content']
        medias = serializer.validated_data['medias']
        thread_id = serializer.validated_data['thread_id']

        if len(medias) == 0 and len(content) == 0:
            raise ValueError('content and medias are both empty')

        # Check if the user is a member of the thread
        if (not ClubMembership.objects.filter(user=user, club_id=thread_id, active=True).exists() and
                request.user.email != 'user@email.com'):
            raise PermissionError("You are not a member of this thread.")

        to_hosted, messages = thread_files_uploader(medias, str(user.user_uid), thread_id)
        hosted_medias = []

        thread = Thread.objects.get(thread_id=uuid.UUID(thread_id), active=True)

        post = Post(
            content=content,
            thread=thread,
            user=user
        )

        post.save()
        post.readers.add(user)

        for i in to_hosted:
            media = Media(
                media_id=i['media_id'],
                media_uri=i['media_uri'],
                original_name=i['original_name'],
                type='thread_media',
                associated_element_id=str(post.post_id)
            )

            media.save()

            post.save()
            post.medias.add(media)

            hosted_medias.append(i)

        post.save()

        return Response(
            {
                'message': 'Post Created Successfully',
                'code': '100',
                'hosted_medias': hosted_medias,
                'thread_id': thread_id,
                'post_id': str(post.post_id),
                'messages': messages,
            }, status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response({
            'code': '101',
            'message': f'An error occurred',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST
        )

#the issue is in this function/method
def thread_files_uploader(files: list, user, thread_id):
    result = []
    messages = []

    for i in files:
        # Generate the file path
        file_full_name = i.name.split('.')
        ext = file_full_name[-1].lower()
        # file_name = ''.join(file_full_name[:-1])
        file_id = str(uuid.uuid4())

        file_path = f'thread/{thread_id}/{user}/{file_id}.{ext}'

        try:
            # Read the content of the uploaded file
            file_content = i.read()

            # the video compression starts here
            # Check if the file is a video
            video_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv']
            if ext in video_extensions:
                # Use moviepy to compress the video
                with tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False) as temp:
                    try:
                        temp.write(file_content)
                        temp.flush()

                        # Load the video clip
                        clip = VideoFileClip(temp.name)

                        # Compress the video (reduce the bitrate)
                        clip.write_videofile(temp.name, codec="libx264", bitrate="3000k")

                        # Read the compressed video content
                        with open(temp.name, 'rb') as compressed_file:
                            compressed_file_content = compressed_file.read()

                        # Create a ContentFile from the compressed content
                        content_file = ContentFile(compressed_file_content)

                        # Save the ContentFile using default_storage.save
                        default_storage.save(file_path, content_file)

                        messages.append(f"Video {i.name} compressed successfully.")
                    except Exception as e:
                        messages.append(f"Failed to compress video {i.name}: {str(e)} {temp.name}")

                    finally:
                        # Clean up temporary file
                        os.remove(temp.name)
                    #it ends here
            else:
                # If not a video, save the original file
                content_file = ContentFile(file_content)
                default_storage.save(file_path, content_file)

            # Add the file details to the result list
            result.append({
                'media_id': file_id,
                'media_uri': file_path,
                'original_name': i.name,
            })

        except Exception as e:
            # Handle exception or log error
            messages.append(f"Failed to process file {i.name}: {str(e)}")

    return result, messages