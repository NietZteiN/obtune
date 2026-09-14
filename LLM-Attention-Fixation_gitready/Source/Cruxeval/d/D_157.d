import std.math;
import std.typecons;
import std.array;

long f(string phrase) 
{
    long ans = 0;
    foreach(word; phrase.split(" "))
    {
        foreach(ch; word)
        {
            if (ch == '0')
            {
                ans++;
            }
        }
    }
    return ans;
}
unittest
{
    alias candidate = f;

    assert(candidate("aboba 212 has 0 digits") == 1L);
}
void main(){}
