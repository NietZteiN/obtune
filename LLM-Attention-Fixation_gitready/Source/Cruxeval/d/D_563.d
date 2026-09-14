import std.math;
import std.typecons;

long f(string text1, string text2) 
{
    long sum = 0;
    foreach (char c; text2)
    {
        foreach (char char1; text1)
        {
            if (char1 == c)
            {
                sum++;
            }
        }
    }
    return sum;
}
unittest
{
    alias candidate = f;

    assert(candidate("jivespdcxc", "sx") == 2L);
}
void main(){}
