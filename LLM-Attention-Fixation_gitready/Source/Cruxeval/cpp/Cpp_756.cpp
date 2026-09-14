#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    if (text.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") == std::string::npos 
        && !text.empty() 
        && std::find_if(text.begin(), text.end(), ::isalpha) != text.end()
        && std::all_of(text.begin(), text.end(), ::isdigit)) 
    {
        return "integer";
    }
    return "string";
}
int main() {
    auto candidate = f;
    assert(candidate(("")) == ("string"));
}
