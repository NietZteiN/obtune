#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string letters) {
    int start = 0;
    int end = letters.length()-1;
    while(start <= end) {
        if(letters[start] == '.' || letters[start] == ',' || letters[start] == '!' || letters[start] == '?' || letters[start] == '*' || letters[start] == ' ') {
            start++;
        } else if(letters[end] == '.' || letters[end] == ',' || letters[end] == '!' || letters[end] == '?' || letters[end] == '*' || letters[end] == ' ') {
            end--;
        } else {
            break;
        }
    }
    letters = letters.substr(start, end-start+1);
    
    for(int i=0; i<letters.length(); i++) {
        if(letters[i] == ' ') {
            letters.replace(i, 1, "....");
            i += 3;
        }
    }
    return letters;
}
int main() {
    auto candidate = f;
    assert(candidate(("h,e,l,l,o,wo,r,ld,")) == ("h,e,l,l,o,wo,r,ld"));
}
