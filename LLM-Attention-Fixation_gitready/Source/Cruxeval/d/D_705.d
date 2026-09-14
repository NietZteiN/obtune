import std.math;
import std.typecons;
string[] f(string[] cities, string name) 
{
    if (name.length == 0) {
        return cities;
    }
    if (name.length != 0 && name != "cities") {
        return [];
    }
    string[] result;
    foreach (city; cities) {
        result ~= name ~ city;
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate(["Sydney", "Hong Kong", "Melbourne", "Sao Paolo", "Istanbul", "Boston"], "Somewhere ") == []);
}
void main(){}
