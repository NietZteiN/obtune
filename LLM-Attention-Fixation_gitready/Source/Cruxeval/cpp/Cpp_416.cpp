#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string old, std::string new_string) {
    std::string result = text;
    size_t index = result.rfind(old);
    while (index > 0 && index < result.find(old)) {
        result.replace(index, old.length(), new_string);
        index = result.rfind(old, index);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("jysrhfm ojwesf xgwwdyr dlrul ymba bpq"), ("j"), ("1")) == ("jysrhfm ojwesf xgwwdyr dlrul ymba bpq"));
}
