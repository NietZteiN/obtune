import std.math;
import std.typecons;
import std.string;

string f(string url) 
{
    if (url.startsWith("http://www."))
    {
        return url[10..$];
    }
    return url;
}
unittest
{
    alias candidate = f;

    assert(candidate("https://www.www.ekapusta.com/image/url") == "https://www.www.ekapusta.com/image/url");
}
void main(){}
