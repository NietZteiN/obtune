import std.math;
import std.typecons;
import std.ascii;

bool f(string text) 
{
    bool b = true;
    foreach (x; text)
    {
        if (x.isDigit)
        {
            b = true;
        }
        else
        {
            b = false;
            break;
        }
    }
    return b;
}
unittest
{
    alias candidate = f;

    assert(candidate("-1-3") == false);
}
void main(){}
