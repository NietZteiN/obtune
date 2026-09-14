import std.math;
import std.typecons;
import std.string;

string g, field;

string f(string text) 
{
    field = text.replace(" ", "");
    g = text.replace("0", " ");
    text = text.replace("1", "i");

    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("00000000 00000000 01101100 01100101 01101110") == "00000000 00000000 0ii0ii00 0ii00i0i 0ii0iii0");
}
void main(){}
