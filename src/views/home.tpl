% include('header.tpl', title=name)



<div class=" h-100 d-flex justify-content-center align-items-center p-5">
	<a class="btn btn-success" href="/upload" role="button">Upload new image</a>
</div>

<div class="container">
	<div class="row text-center text-lg-left">
	% for item in items:
		<div class="col-lg-3 col-md-4 col-xs-6">
			<div class="card" style="width: 18rem; height: 25rem">
				<img class="card-img-top" src="{{item.get('url')}}" alt="{{item.get('category')}}" >
				<div class="card-body">
					<h5 class="card-title">{{item.get('category')}}</h5>
					<a class="btn btn-primary float-left" download="Boto"  href="{{item.get('url')}}" role="button">Download</a>
					<form method="GET" action="/delete" enctype="multipart/form-data">
						<input type="number" name="id" value="{{item.get('id')}}" class="d-none">
							<button type="submit" class="btn btn-danger float-right"> Delete </button>
					</form>
				</div>
			</div>
		</div>
	% end

	</div>
</div>

% include('footer.tpl')
