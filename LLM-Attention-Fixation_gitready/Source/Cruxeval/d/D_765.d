import std.math;
import std.typecons;
long f(string text) 
{
    int count = 0;
    foreach (char c; text)
    {
        if (c >= '0' && c <= '9')
        {
            count++;
        }
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate("so456") == 3L);
}
void main(){}
