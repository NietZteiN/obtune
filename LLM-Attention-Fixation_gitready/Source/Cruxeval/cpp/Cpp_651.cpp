#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string letter) {
    if(islower(letter[0])) letter[0] = toupper(letter[0]);
    for(int i=0; i<text.size(); i++)
    {
        if(text[i] == letter[0])
        {
            text[i] = letter[0];
        }
    }
    text[0] = toupper(text[0]);
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("E wrestled evil until upperfeat"), ("e")) == ("E wrestled evil until upperfeat"));
}
