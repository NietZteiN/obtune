import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

Nullable!(string[string]) f(string[] seq, string value) 
{
    string[string] roles;
    foreach (s; seq)
    {
        roles[s] = "north";
    }

    if (value.length != 0)
    {
        auto splitValues = value.split(", ");
        foreach (val; splitValues)
        {
            roles[val.strip()] = "north";
        }
    }
    return roles.nullable;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(["wise king", "young king"], "");
        assert(!result.isNull && result.get == ["wise king": "north", "young king": "north"]);
}

}
void main(){}
