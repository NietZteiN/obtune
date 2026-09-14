import std.math;
import std.typecons;
import std.array;
import std.string;

long f(string text) 
{
    auto s = text.splitLines();
    return s.length;
}
unittest
{
    alias candidate = f;

    assert(candidate("145

12fjkjg") == 3L);
}
void main(){}
