import std.math;
import std.typecons;
long f(string s) 
{
    foreach (i; 0 .. s.length)
    {
        if (s[i] >= '0' && s[i] <= '9')
        {
            return i + (s[i] == '0' ? 1 : 0);
        }
        else if (s[i] == '0')
        {
            return -1;
        }
    }
    
    return -1;
}
unittest
{
    alias candidate = f;

    assert(candidate("11") == 0L);
}
void main(){}
