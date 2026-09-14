import std.math;
import std.typecons;
import std.string;
import std.ascii;

string f(string text) 
{
    size_t uppers = 0;
    foreach (c; text)
    {
        if (isUpper(c))
        {
            uppers++;
        }
    }
    
    return uppers >= 10 ? text.toUpper : text;
}
unittest
{
    alias candidate = f;

    assert(candidate("?XyZ") == "?XyZ");
}
void main(){}
