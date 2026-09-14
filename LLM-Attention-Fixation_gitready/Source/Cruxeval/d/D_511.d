import std.math;
import std.typecons;
import std.array;

Nullable!(string[string]) f(Tuple!(string, string, string) fields, Nullable!(string[string]) update_dict) 
{
    if (fields.empty || update_dict.isNull) {
        return Nullable!(string[string]).init;
    }
    string[string] di;
    foreach (field; fields) {
        di[field] = "";
    }
    foreach (key, value; update_dict.get()) {
        di[key] = value;
    }
    return Nullable!(string[string])(di);
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(tuple("ct", "c", "ca"), ["ca": "cx"].nullable);
        assert(!result.isNull && result.get == ["ct": "", "c": "", "ca": "cx"]);
}

}
void main(){}
