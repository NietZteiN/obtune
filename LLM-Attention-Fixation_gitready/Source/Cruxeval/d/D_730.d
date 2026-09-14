import std.math;
import std.typecons;
import std.array;
import std.string;

long f(string text) 
{
    long m = 0;
    long cnt = 0;
    foreach (word; text.split(" "))
    {
        if (word.length > m)
        {
            cnt++;
            m = word.length;
        }
    }
    return cnt;
}
unittest
{
    alias candidate = f;

    assert(candidate("wys silak v5 e4fi rotbi fwj 78 wigf t8s lcl") == 2L);
}
void main(){}
