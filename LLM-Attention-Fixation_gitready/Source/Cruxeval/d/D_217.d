import std.math;
import std.typecons;
import std.ascii;
import std.string;

string f(string str) 
{
    bool isAlphaNumeric = true;
    foreach (char c; str)
    {
        if (!isAlpha(c) && !isDigit(c))
        {
            isAlphaNumeric = false;
            break;
        }
    }

    if (isAlphaNumeric) 
    {
        return "ascii encoded is allowed for this language";
    }
    return "more than ASCII";
}
unittest
{
    alias candidate = f;

    assert(candidate("Str zahrnuje anglo-ameriæske vasi piscina and kuca!") == "more than ASCII");
}
void main(){}
