<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="icon" href="favi.png">

    <title>Clasificá Chistes y Divertite - pgHumor</title>

    <!-- Bootstrap core CSS -->
    <link href="dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="dist/css/bootstrap-theme.min.css" rel="stylesheet">
    <link href="estilo.css" rel="stylesheet">

    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <script src="logic.js"></script>

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>

  <body>

    <div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
            <span class="sr-only">pgHumor</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a id="Home" class="navbar-brand" href="#" onclick="Home();">pgHumor</a>
        </div>
        <div class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li id="aboutUs"><a  href="#" onclick="aboutUs();">Quiénes Somos?</a></li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </div>

    <div class="container">

      <div id="HomeText" class="starter-template">
        <p class="lead" id="Chiste"></p>
            <button type="button" class="btn btn-lg btn-success chiste" onclick="procesar('c');">Humor</button>
            <button type="button" class="btn btn-lg btn-default" onclick="procesar('r');">Repetido</button>
            <button type="button" class="btn btn-lg btn-info" onclick="procesar('n');">Nose</button>
            <button type="button" class="btn btn-lg btn-danger cualquiera" onclick="procesar('x');">Cualquiera</button>    
      </div>

      <div id="aboutUsText" class="starter-template">
        <p class="lead">Somos dos estudiantes (Santiago Castro y Matías Cubero) de Ingeniería en Computación que estamos realizando un proyecto de grado que pretende detectar humor en textos en español. Para esto necesitamos obtener una base de datos de chistes en español. Gracias a tu ayuda, vamos a poder obtener una base de datos de buena calidad.<br><br> ¡¡¡MUCHAS GRACIAS!!! </p>
      </div>
      
      

    </div><!-- /.container -->
    <hr>
    <footer>
        <p>&copy; pgHumor 2014</p>
      </footer>

    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="../../dist/js/bootstrap.min.js"></script>
    <script>
      (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
      (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
      m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
      })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

      ga('create', 'UA-34392230-5', 'auto');
      ga('send', 'pageview');

    </script>
  </body>
</html>
