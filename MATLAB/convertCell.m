function [finalArray] = convertCell(cellArray)

finalArray = [];
[row col]=size(cellArray);
for n=1:row
    finalArray = [finalArray str2num(cellArray{n})];
end

end
