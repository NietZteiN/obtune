import std.math;
import std.typecons;

string f(string text, long position, string value) 
{
    long length = text.length;
    long index = (position % (length + 2)) - 1;
    if (index >= length || index < 0) {
        return text;
    }
    auto text_list = text.dup;
    text_list[index] = value[0];
    return text_list.idup;
}
unittest
{
    alias candidate = f;

    assert(candidate("1zd", 0L, "m") == "1zd");
}
void main(){}
