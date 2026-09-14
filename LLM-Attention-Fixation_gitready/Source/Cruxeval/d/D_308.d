import std.math;
import std.typecons;

Nullable!(long[string]) f(string[] strings) 
{
    long[string] occurances;
    foreach (string s; strings)
    {
        long count = 0;
        foreach (string str; strings)
        {
            if (str == s)
            {
                count++;
            }
        }
        
        if (occurances.get(s, -1) == -1)
        {
            occurances[s] = count;
        }
    }
    
    return Nullable!(long[string])(occurances);
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(["La", "Q", "9", "La", "La"]);
        assert(!result.isNull && result.get == ["La": 3L, "Q": 1L, "9": 1L]);
}

}
void main(){}
