#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string new_value, long index) {
    std::string new_text = text;
    if(index < text.length()){
        std::replace(new_text.begin(), new_text.end(), text[index], new_value[0]);
    }
    return new_text;
}
int main() {
    auto candidate = f;
    assert(candidate(("spain"), ("b"), (4)) == ("spaib"));
}
