#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long width) {
    std::string output = text.substr(0, width);
    while(output.size() < width) {
        output.insert(0, "z");
        if(output.size() < width) output.push_back('z');
    }
    return output;
}
int main() {
    auto candidate = f;
    assert(candidate(("0574"), (9)) == ("zzz0574zz"));
}
