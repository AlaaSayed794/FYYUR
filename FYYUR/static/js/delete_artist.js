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
	