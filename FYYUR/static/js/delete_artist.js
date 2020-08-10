const button_delete = document.querySelectorAll('[id=delete-btn]')[0];
button_delete.onclick = function(e)
	{
		const artistItem = e.target.dataset['id'];
		fetch('/artists/' + artistItem + '/Delete', {
				method:'DELETE'
				,
				cache: "reload",
				headers: {
					'Content-Type' :'application/json'
				}}).then(function(){
			
			
			window.location.href ='/artists'
			
		}).catch(function() {
	        window.location.href ='/'
	    })
	}

	const button_delete_shows = document.querySelectorAll('[id=delete-show]');
	for(let i =0 ; i < button_delete_shows.length ; i++)
	{
		const button_delete_show = button_delete_shows[i]
		
		button_delete_show.onclick = function(e)
		{
			
			const artist = e.target.dataset['artist'];
			const showItem = e.target.dataset['id'];
			fetch('/shows/' + showItem + '/Delete', {
					method:'DELETE'
					,
					cache: "reload",
					headers: {
						'Content-Type' :'application/json'
					}}).then(function(){
				
				
				window.location.href ='/artists/' +artist
				
			}).catch(function() {
				window.location.href ='/'
			})
		}

	}