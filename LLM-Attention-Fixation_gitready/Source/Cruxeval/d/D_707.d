import std.math;
import std.typecons;
import std.array;

string f(string text, long position) 
{
    long length = text.length;
    long index = position % (length + 1);
    if (position < 0 || index < 0)
        index = -1;
    text = text[0 .. index] ~ text[index+1 .. $];
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("undbs l", 1L) == "udbs l");
}
void main(){}
