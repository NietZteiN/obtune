import std.math;
import std.typecons;
import std.algorithm;
import std.string;

long f(string full, string part) 
{
    long length = part.length;
    long index = full.indexOf(part);
    long count = 0;
    while (index >= 0)
    {
        full = full[index + length .. $];
        index = full.indexOf(part);
        count++;
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate("hrsiajiajieihruejfhbrisvlmmy", "hr") == 2L);
}
void main(){}
