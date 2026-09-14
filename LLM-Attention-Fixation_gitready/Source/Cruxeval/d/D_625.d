import std.math;
import std.typecons;
import std.string;

long f(string text) 
{
    long count = 0;
    foreach (i; text)
    {
        if (i == '.' || i == '?' || i == '!' || i == ',' || i == '.')
        {
            count++;
        }
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate("bwiajegrwjd??djoda,?") == 4L);
}
void main(){}
