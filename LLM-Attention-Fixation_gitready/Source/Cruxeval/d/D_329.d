import std.math;
import std.typecons;
import std.ascii;

bool f(string text) 
{
    foreach(i; 1 .. text.length)
    {
        if (text[i] == toUpper(text[i]) && isLower(text[i-1]))
        {
            return true;
        }
    }
    return false;
}
unittest
{
    alias candidate = f;

    assert(candidate("jh54kkk6") == true);
}
void main(){}
