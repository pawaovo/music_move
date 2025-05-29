# 准备结果收集
        successfully_matched_songs = []
        
        # 定义搜索函数
        async def search_func(parsed_song):
            # 使用项目级别客户端进行搜索
            return await search_song_on_spotify_sync_wrapped(
                parsed_song, 
                semaphore=semaphore,
                spotify_client=spotify_client
            )
        
        # 结果回调函数
        async def on_song_result(original_line, title, artists, norm_title, norm_artists, search_result):
            if search_result:
                successfully_matched_songs.append(search_result)
        
        # 处理歌曲列表
        total, matched, failed = await process_song_list_file(
            file_path=temp_path,
            normalizer=normalizer,
            spotify_search_func=search_func,
            on_result_callback=on_song_result,
            batch_size=request.batch_size,
            max_concurrency=request.concurrency
        ) 