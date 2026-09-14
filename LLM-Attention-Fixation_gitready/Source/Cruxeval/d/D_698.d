import std.math;
import std.typecons;
string f(string text) 
{
    string result;
    foreach (x; text)
    {
        if (x != ')')
        {
            result ~= x;
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("(((((((((((d))))))))).))))(((((") == "(((((((((((d.(((((");
}
void main(){}
