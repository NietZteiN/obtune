import std.math;
import std.typecons;
long f(string txt) 
{
    auto coincidences = new AssociativeArray!(char, int);
    
    foreach (c; txt)
    {
        if (c in coincidences)
        {
            coincidences[c]++;
        }
        else
        {
            coincidences[c] = 1;
        }
    }
    
    int sum = 0;
    foreach (value; coincidences.byValue)
    {
        sum += value;
    }
    
    return sum;
}
unittest
{
    alias candidate = f;

    assert(candidate("11 1 1") == 6L);
}
void main(){}
