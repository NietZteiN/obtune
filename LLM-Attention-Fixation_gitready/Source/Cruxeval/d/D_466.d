import std.math;
import std.typecons;
import std.ascii;

string f(string text) 
{
    size_t length = text.length;
    size_t index = 0;
    while (index < length && isWhite(text[index]))
    {
        index++;
    }
    return text[index .. index + 5];
}
unittest
{
    alias candidate = f;

    assert(candidate("-----	
	th
-----") == "-----");
}
void main(){}
