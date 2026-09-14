import std.math;
import std.typecons;
import std.string;

string f(string text, long position, string value) 
{
    long length = text.length;
    long index = position % length;
    if (position < 0)
    {
        index = length / 2;
    }
    auto new_text = text.replace(index, index, value);
    new_text = new_text[0 .. $-2] ~ new_text[$-1 .. $];
    return new_text;
}
unittest
{
    alias candidate = f;

    assert(candidate("sduyai", 1L, "y") == "syduyi");
}
void main(){}
