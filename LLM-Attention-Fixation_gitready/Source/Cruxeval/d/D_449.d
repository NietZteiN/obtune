import std.math;
import std.typecons;
import std.ascii;

bool f(string x) 
{
    auto n = x.length;
    auto i = 0;
    while (i < n && isDigit(x[i]))
    {
        i++;
    }
    return i == n;
}
unittest
{
    alias candidate = f;

    assert(candidate("1") == true);
}
void main(){}
