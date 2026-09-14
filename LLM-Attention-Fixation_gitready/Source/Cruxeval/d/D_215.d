import std.math;
import std.typecons;
string f(string text) 
{
    string new_text = text;
    while (text.length > 1 && text[0] == text[$ - 1]) {
        new_text = text = text[1..$-1];
    }
    return new_text;
}
unittest
{
    alias candidate = f;

    assert(candidate(")") == ")");
}
void main(){}
