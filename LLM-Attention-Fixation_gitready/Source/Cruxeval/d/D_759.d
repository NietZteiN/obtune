import std.math;
import std.typecons;
import std.string;

long[] f(string text, string sub) 
{
    long[] index;
    long starting = 0;
    while (starting != -1)
    {
        starting = text.indexOf(sub, starting);
        if (starting != -1)
        {
            index ~= starting;
            starting += sub.length;
        }
    }
    return index;
}
unittest
{
    alias candidate = f;

    assert(candidate("egmdartoa", "good") == []);
}
void main(){}
