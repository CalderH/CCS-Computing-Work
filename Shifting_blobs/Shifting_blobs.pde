import java.util.ArrayList;

class Blob
{
  float x, y;
  float dir;
  float change;
  
  Blob ( float x_, float y_, float dir_ )
  {
    x = x_;
    y = y_;
    dir = dir_;
    change = 0;
  }
  
  float getX()
  {
    return x;
  }
  
  float getY()
  {
    return y;
  }
  
  void display()
  {
    ellipse(x, y, 10, 10);
  }
  
  void move()
  {
    float xvel = sin( dir ) * 3;
    float yvel = cos( dir ) * 3;
    
    if ( x <= boxLeft || x >= boxRight )
    {
      xvel *= -1;
    }
    
    if ( y <= boxTop || y >= boxBottom )
    {
      yvel *= -1;
    }
   
    dir = atan2( xvel, yvel );
    change = random( lerp( -.3, .25, ( change + 0.3 ) / 0.6 ), lerp( -.25, .3, ( change + 0.3 ) / 0.6 ) );
    change = random( lerp( -.2, .15, ( change + 0.2 ) / 0.4 ), lerp( -.15, .2, ( change + 0.2 ) / 0.4 ) );
    dir += change;
    
    x += sin( dir );
    y += cos( dir );
  }
}

ArrayList<Blob> blobs;
int numBlobs = 20;
int radius = 500;
int threshold = 1400000;
int screenWidth = 960;
int screenHeight = 540;
int boxWidth = screenHeight;
int boxHeight = screenHeight;
int boxLeft = screenWidth / 2 - boxWidth / 2;
int boxRight = screenWidth /2  + boxWidth / 2;
int boxTop = screenHeight / 2 - boxHeight / 2;
int boxBottom = screenHeight / 2 + boxHeight / 2;
int stage = 0;

void setup()
{
  size(960, 540);
  pixelDensity(2);
  blobs = new ArrayList<Blob>();
  for ( int i = 0; i < numBlobs; i++ )
  {
    blobs.add( new Blob( random(boxLeft, boxRight), random(boxTop, boxBottom), random( TWO_PI ) ) );
  }
}

void draw()
{
  loadPixels();
  
  for ( int x = 0; x < width * 2; x++ )
  {
    for ( int y = 0; y < height * 2; y++ )
    {
      float sum = 0;
      for ( Blob b : blobs )
      {
        float thisOne = radius - dist( float(x) / 2, float(y) / 2, b.getX(), b.getY() );
        if ( thisOne < 0 )
        {
          thisOne = 0;
        }
        thisOne = thisOne * thisOne;
        sum += thisOne;
      }

      if (sum >= threshold)
      {
        pixels[ 2 * width * y + x ] = color( 0 );
      }
      else
      {
        pixels[ 2 * width * y + x ] = color( 255 );
      }
    }
  }
  
  updatePixels();
  
  for ( Blob b : blobs )
  {
    b.move();
  }
}
