import std.math;
import std.typecons;
import std.string;

bool f(string t) 
{
    foreach (c; t)
    {
        if (c < '0' || c > '9')
        {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate("#284376598") == false);
}
void main(){}
