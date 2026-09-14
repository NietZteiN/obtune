import std.math;
import std.typecons;
import std.algorithm;

bool f(string s) 
{
    int count0 = 0;
    int count1 = 0;
    
    foreach (char c; s)
    {
        if (c == '0')
            count0++;
        else if (c == '1')
            count1++;
    }
    
    return s.length == count0 + count1;
}
unittest
{
    alias candidate = f;

    assert(candidate("102") == false);
}
void main(){}
