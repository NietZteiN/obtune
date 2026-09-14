#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string) {
    if(std::all_of(string.begin(), string.end(), ::isalnum)) {
        return "ascii encoded is allowed for this language";
    }
    return "more than ASCII";
}
int main() {
    auto candidate = f;
    assert(candidate(("Str zahrnuje anglo-ameriæske vasi piscina and kuca!")) == ("more than ASCII"));
}
