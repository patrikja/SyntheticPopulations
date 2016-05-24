module Example1 where
import Data.List (intersperse)
import Draft

-- Example: Assume we have only two attributes, Age and Income.

data Age    = Child | Mid | Old      deriving (Eq, Ord, Show, Bounded, Enum)
data Income = Poor | Middle | Rich   deriving (Eq, Ord, Show, Bounded, Enum)

instance All Age
instance All Income

type ID     = Integer

data Agent = A {aid :: ID, aage :: Age, aincome :: Income}
  deriving (Eq, Ord, Show)

fullPop :: [Agent]
fullPop = [ A 00 Child Middle
          , A 01 Child Middle
          , A 02 Mid   Middle
          , A 03 Mid   Middle
          , A 04 Child Middle
          , A 05 Mid   Middle
          , A 06 Mid   Middle
          , A 07 Child Poor
          , A 08 Child Poor
          , A 09 Child Poor
          , A 10 Mid   Poor
          , A 11 Old   Rich
          , A 12 Old   Rich
          , A 13 Child Rich
          , A 14 Child Rich
          , A 15 Mid   Rich
          ]

-- Compute histograms from the full population
hista :: Hist1 Age
hista = histogram1 aage    fullPop
histb :: Hist1 Income
histb = histogram1 aincome fullPop

-- Pick a few agents as the small population
smallPop :: [Agent]
smallPop = take 6 (drop 6 fullPop)
smallPopProblem1 = take 3 (drop 9 fullPop)

-- Now compute a 2-D histogram for smallPop to start population generaton from

s2 :: Hist2 Age Income
s2 = histogram2 aage aincome smallPop

-- Just for comparison, here is the full histogram
f2 :: Hist2 Age Income
f2 = histogram2 aage aincome fullPop

-- Now for the scaling up of s2
s2_1 = scale hista histb s2
s2_2 = scale hista histb s2_1
s2_3 = scale hista histb s2_2

-- TODO problem 1: if a row or column in s2 is all zeros we get divide by zero error. This makes the whole mid column NaN.
-- TODO problem 2: if any box in hab is zero, it will stay zero through all the scaling (and this does not feel right)

main = do print smallPop
          putStrLn (showHist hista)
          putStrLn (showHist histb)
          putStrLn (showHist2 s2_3)
          putStrLn (showHist2 f2)
