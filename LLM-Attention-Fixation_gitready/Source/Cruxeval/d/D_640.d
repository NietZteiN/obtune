import std.math;
import std.typecons;
import std.string;
import std.algorithm.searching;

long f(string text) 
{
    long a = 0;
    if (text.indexOf(text[0], 1) != -1)
    {
        a += 1;
    }
    for (long i = 0; i < text.length - 1; ++i)
    {
        if (text.indexOf(text[i], i + 1) != -1)
        {
            a += 1;
        }
    }
    return a;
}
unittest
{
    alias candidate = f;

    assert(candidate("3eeeeeeoopppppppw14film3oee3") == 18L);
}
void main(){}
