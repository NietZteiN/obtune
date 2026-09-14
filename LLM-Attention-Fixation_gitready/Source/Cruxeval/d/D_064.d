import std.math;
import std.typecons;
string f(string text, long size) 
{
    ulong counter = text.length;
    for (long i = 0; i < size - cast(long)(size % 2); i++)
    {
        text = " " ~ text ~ " ";
        counter += 2;
        if (counter >= size)
        {
            return text;
        }
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("7", 10L) == "     7     ");
}
void main(){}
