import std.math;
import std.typecons;
import std.string;

bool f(string text) 
{
    auto length = text.length;
    auto half = cast(size_t)(length / 2);
    auto encode = text[0 .. half].dup.toStringz;
    
    if (text[half .. $] == encode.fromStringz)
        return true;
    else
        return false;
}
unittest
{
    alias candidate = f;

    assert(candidate("bbbbr") == false);
}
void main(){}
